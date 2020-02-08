#include "priority_queue.h"
#include "attendee.h"

#include <sstream>

void PriorityQueue::bind(pybind11::module &m) {
  pybind11::class_<PriorityQueue, PriorityQueue::pointer_t> o(
      m, "PriorityQueue", R"pbdoc(
A priority-based queue of queues.

Some derivations of this object may also block access to the
append() function, requiring the user to add items to the queue
through some other method.
)pbdoc");

  o.def(pybind11::init<>());

  o.def("push_future", &PriorityQueue::push_future,
        R"pbdoc(
Schedule an item to be posted at low priority at a future time.
:param item: The item to add.
:param delay_in_sec: The minimum number of seconds before the item can
        be picked up from the queue (defaults to zero).
)pbdoc",
        pybind11::arg("item"), pybind11::arg("delay_in_sec") = 0.0);

  o.def("push_high", &PriorityQueue::push_high,
        R"pbdoc(
Add a high priority item to the queue.
A high priority item will be processed before any lower priority items.
:param item: The item to add.
)pbdoc",
        pybind11::arg("item"));

  o.def("push_low", &PriorityQueue::push_low,
        R"pbdoc(
Add an item to the queue.
:param item: The item to add.
)pbdoc",
        pybind11::arg("item"));

  o.def("get", &PriorityQueue::get,
        R"pbdoc(
Pop an item off the queue and return it.

:param purge_if_high: If True and the item fetched is of high priority,
    purge any low or future items from the queue.
:returns: The item, or None if the queue was empty.
)pbdoc",
        pybind11::arg("purge_if_high") = true);

  o.def("__bool__", [](PriorityQueue &a) { return !a.empty(); },
        R"pbdoc(
Returns True if the queue has items that can be retrieved with get().

Future items are not retrievable with get() until their time delay
has expired.  As a result, if there are only future items in the queue,
False will be returned.

This attribute is read-only.
)pbdoc");

  o.def("__repr__",
        [](const PriorityQueue &) { return "<thread_meeting.PriorityQueue>"; });
}

void PriorityQueue::push_future(pybind11::object obj, float delay_in_seconds) {
  low_t temp;
  auto milliseconds = static_cast<unsigned>(delay_in_seconds * 1000);
  temp.when += std::chrono::milliseconds(milliseconds);
  temp.what = obj;
  m_future_q.push(temp);
}

void PriorityQueue::push_high(pybind11::object obj) { m_high_q.push_back(obj); }

void PriorityQueue::push_low(pybind11::object obj) { m_low_q.push_back(obj); }

bool PriorityQueue::empty() {
  while (!m_future_q.empty()) {
    auto &item = m_future_q.top();
    auto now = std::chrono::steady_clock::now();
    if (now >= item.when) {
      // It's time to put the item in the queue!
      m_low_q.push_back(item.what);
      m_future_q.pop();
    } else {
      // The queue only holds future events.
      break;
    }
  }
  return m_high_q.empty() && m_low_q.empty();
}

pybind11::object PriorityQueue::get(bool purge_if_high) {
  pybind11::object result = pybind11::none();
  auto priority = Priority::low;
  if (!empty()) {
    if (!m_high_q.empty()) {
      result = std::move(m_high_q.front());
      m_high_q.pop_front();
      priority = Priority::high;
    } else {
      result = std::move(m_low_q.front());
      m_low_q.pop_front();
      priority = Priority::low;
    }
  }

  if (purge_if_high && Priority::high == priority) {
    auto items_dropped = 0U;
    items_dropped += m_low_q.size();
    m_low_q.clear();
    while (!m_future_q.empty()) {
      ++items_dropped;
      m_future_q.pop();
    }
    if (items_dropped) {
      std::stringstream sstr;
      sstr << "Purged: " << items_dropped << " items";
      transcribe(sstr.str(), TranscriptType::debug);
    }
  }
  return result;
}
