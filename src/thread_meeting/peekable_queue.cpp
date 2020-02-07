#include "peekable_queue.h"
#include "attendee.h"

#include <sstream>

void PeekableQueue::bind(pybind11::module &m) {
  pybind11::class_<PeekableQueue, PeekableQueue::pointer_t> o(
      m, "PeekableQueue", R"pbdoc(
A FIFO Queue with limited access to members other than head.

Some derivations of this object may also block access to the
append() function, requiring the user to add items to the queue
through some other method.
)pbdoc");

  o.def(pybind11::init<>());

  o.def_property_readonly("head", &PeekableQueue::head,
                          R"pbdoc(
The next item in the queue or None if not available.
This attribute is read-only.
)pbdoc");

  o.def("append", &PeekableQueue::append,
        R"pbdoc(
Push an item on the back of the queue.
:param item: The item to add.
:param delay_in_sec: The minimum number of seconds before the item can
        be picked up from the queue (defaults to zero).

Some derivations of this object may also block access to the append()
function, requiring the user to add items to the queue through some
other method.  If append() is blocked, a ValueError is raised.
)pbdoc",
        pybind11::arg("item"), pybind11::arg("delay_in_sec") = 0);

  o.def("get", &PeekableQueue::get,
        R"pbdoc(
Pop an item off the queue and return it.
:returns: The item, or None if the queue was empty.
)pbdoc");

  o.def("__bool__", [](PeekableQueue &a) { return !a.empty(); },
        R"pbdoc(
Returns True if the queue has items that can be retrieved with get().

Delayed items are not retrievable with get() until their time delay
has expired.  As a result, if there are only delayed items in the queue,
False will be returned.

This attribute is read-only.
)pbdoc");

  o.def("__repr__",
        [](const PeekableQueue &) { return "<thread_meeting.PeekableQueue>"; });
}

void PeekableQueue::append(pybind11::object obj, int delay_in_seconds) {
  if (m_disable_append) {
    throw std::invalid_argument("append() disabled on this PeekableQueue");
  }
  push(std::move(obj), delay_in_seconds);
}

bool PeekableQueue::empty() {
  while (!m_low.empty()) {
    auto &item = m_low.top();
    auto now = std::chrono::steady_clock::now();
    if (now >= item.when) {
      // It's time to put the item in the queue!
      m_medium.push_back(item.what);
      m_low.pop();
    } else {
      // The queue only holds future events.
      break;
    }
  }
  return m_high.empty() && m_medium.empty();
}

void PeekableQueue::push(pybind11::object obj, int delay_in_seconds,
                         bool can_purge) {
  empty(); // Make sure any low-priority items that need to be promoted are.
  auto purge = (can_purge && 0 == delay_in_seconds);

  // We need to know if the caller is the Admin to determine
  // the target queue.
  auto caller_is_admin = false;
  if (auto admin = g_admin.lock()) {
    auto my_thread_id = PyThread_get_thread_ident();
    caller_is_admin = (my_thread_id == admin->thread_id());
  }

  if (purge && caller_is_admin) {
    // The Admin dumped all low and medium queue entries.
    auto low_count = 0U;
    while (!m_low.empty()) {
      ++low_count;
      m_low.pop();
    }
    auto medium_count = m_medium.size();
    m_medium.clear();

    std::stringstream sstr;
    sstr << "Purged " << low_count << " delayed and " << medium_count
         << " queued messages";
    transcribe(sstr.str(), TranscriptType::debug);
  }

  if (delay_in_seconds > 0) {
    low_t temp;
    temp.when += std::chrono::seconds(delay_in_seconds);
    temp.what = obj;
    m_low.push(temp);
  } else if (caller_is_admin) {
    m_high.push_back(obj);
  } else {
    m_medium.push_back(obj);
  }
}

pybind11::object PeekableQueue::head() {
  if (empty()) {
    return pybind11::none();
  } else if (m_high.empty()) {
    return m_medium.front();
  } else {
    return m_high.front();
  }
}

pybind11::object PeekableQueue::get() {
  pybind11::object result = pybind11::none();
  if (!empty()) {
    if (!m_high.empty()) {
      result = std::move(m_high.front());
      m_high.pop_front();
    } else {
      result = std::move(m_medium.front());
      m_medium.pop_front();
    }
  }
  return result;
}
