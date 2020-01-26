#include "attendee.h"
#include "baton_scope.h"
#include "interruptable_scope.h"

#include <memory>

void Attendee::bind(pybind11::module &m) {
  pybind11::class_<Attendee, Attendee::pointer_t>(m, "Attendee")
      .def("__repr__",
           [](const Attendee &a) {
             return "<thread_Meeting.Attendee '" + a.name + "'>";
           })
      .def_readonly("name", &Attendee::name)
      .def("note", &Attendee::note)
      .def_property_readonly(
          "queue", [](const Attendee &a) { return pybind11::cast(a.queue); })
      .def("__bool__", [](const Attendee &a) { return a.valid; })
      .def("interrupt_with", &Attendee::create_iterruptable_scope)
      .def("request_baton", &Attendee::request_baton);

  pybind11::register_exception<WakeAttendee>(m, "WakeAttendee");
}

void Attendee::add_to_queue(Take::pointer_t take) {
  auto thread_id = PyThread_get_thread_ident();
  auto trans_type =
      (thread_id == m_thread_id) ? TranscriptType::note : TranscriptType::post;
  transcribe(take->name, trans_type, m_thread_id);
  queue->push(pybind11::cast(take));
  if (!(thread_id == m_thread_id || m_interruptables.empty())) {
    auto top = m_interruptables.top();
    PyThreadState_SetAsyncExc(m_thread_id, top.ptr());
  }
}

std::unique_ptr<Keep> Attendee::note(std::string name,
                                     pybind11::object payload) {
  auto keep = std::make_unique<Keep>(name, payload);
  auto take = keep->create_take();
  add_to_queue(take);
  return keep;
}

std::unique_ptr<EnterExit>
Attendee::create_iterruptable_scope(pybind11::object obj) {
  return std::make_unique<InterruptableScope>(shared_from_this(), obj);
}

std::unique_ptr<EnterExit> Attendee::request_baton() {
  return std::make_unique<BatonScope>(valid);
}
