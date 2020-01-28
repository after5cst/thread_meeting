#include "peekable_queue.h"

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

Some derivations of this object may also block access to the append()
function, requiring the user to add items to the queue through some
other method.  If append() is blocked, a ValueError is raised.
)pbdoc",
        pybind11::arg("item"));

  o.def("get", &PeekableQueue::get,
        R"pbdoc(
Pop an item off the queue and return it.
:returns: The item, or None if the queue was empty.
)pbdoc");

  o.def("__bool__", [](const PeekableQueue &a) { return !a.empty(); },
        R"pbdoc(
Returns True if the queue is empty, False otherwise.
This attribute is read-only.
)pbdoc");

  o.def("__repr__",
        [](const PeekableQueue &) { return "<thread_meeting.PeekableQueue>"; });
}

void PeekableQueue::append(pybind11::object obj) {
  if (m_disable_append) {
    throw std::invalid_argument("append() disabled on this PeekableQueue");
  }
  push(std::move(obj));
}

void PeekableQueue::push(pybind11::object obj) { m_queue.push_back(obj); }

pybind11::object PeekableQueue::head() const {
  return m_queue.empty() ? pybind11::none() : m_queue.front();
}

pybind11::object PeekableQueue::get() {
  pybind11::object result = pybind11::none();
  if (!m_queue.empty()) {
    result = m_queue.front();
    m_queue.pop_front();
  }
  return result;
}
