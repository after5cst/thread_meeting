#include "peekable_queue.h"

void PeekableQueue::bind(pybind11::module &m) {
  pybind11::class_<PeekableQueue, PeekableQueue::pointer_t>(m, "PeekableQueue")
      .def(pybind11::init<>())
      .def_property_readonly("head", &PeekableQueue::head)
      .def("append", &PeekableQueue::append)
      .def("get", &PeekableQueue::get)
      .def("__bool__", [](const PeekableQueue &a) { return !a.empty(); })
      .def("__repr__", [](const PeekableQueue &a) {
        return "<thread_meeting.PeekableQueue>";
      });
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
