#include "take.h"

#include "globals.h"

#include <sstream>

void Take::bind(pybind11::module &m) {
  pybind11::class_<Take, Take::pointer_t> o(m, "Take", R"pbdoc(
A container that holds a name, a message, and a status.

A Keep can create Take objects to send to other recipients, typically
in other threads.  When the recipient marks the Take as Acknowledged or
Protested, or the object goes out of scope, the Keep is notified.

This allows the Keep holder to monitor what Takes are still Pending.
)pbdoc");

  o.def(pybind11::init<std::string, pybind11::object>(),
        R"pbdoc(
Initialization function.

:param name: The name to be assigned to the Take
:param payload: The optional payload object.
)pbdoc",
        pybind11::arg("name") = "",
        pybind11::arg("payload") = pybind11::none());

  o.def_readonly("name", &Take::name,
                 R"pbdoc(
The name passed to the Take during initialization.
This attribute is read-only.
)pbdoc");

  o.def_property_readonly("status", [](Take &a) { return *(a.status); },
                          R"pbdoc(
The current status of the Keep.

The status is set via the acknowledge() or protest() method calls.
It may be only changed once.  The initial value is MessageStatus.Pending.

This attribute is read-only.
)pbdoc");

  o.def("acknowledge", &Take::acknowledge, R"pbdoc(
Set the status of the Take from Pending to Acknowledged.

This attribute is read-only.
)pbdoc");

  o.def_readonly("payload", &Take::payload,
                 R"pbdoc(
The payload passed to the Take during initialization.
This attribute is read-only.
)pbdoc");

  o.def("protest", &Take::protest, R"pbdoc(
Set the status of the Take from Pending to Protested.

This attribute is read-only.
)pbdoc");

  o.def("__repr__",
        [](const Take &a) { return "<thread_meeting.Take '" + a.name + "'>"; });
}

void Take::set_status(MessageStatus new_status, bool throw_on_error) {
  if (*status == new_status) {
    // Do nothing: setting a status to itself is a NOOP.
    return;
  }

  auto trans_type = TranscriptType::custom;
  switch (new_status) {
  case MessageStatus::acknowledged:
    if (MessageStatus::pending == *status) {
      trans_type = TranscriptType::ack;
    }
    break;
  case MessageStatus::protested:
    if (MessageStatus::pending == *status) {
      trans_type = TranscriptType::nack;
    }
    break;
  case MessageStatus::pending:
    break;
  }

  if (TranscriptType::custom != trans_type) {
    transcribe(name, trans_type);
    *status = new_status;

  }
  // If we reach here, there is an error.
  else if (throw_on_error) {
    std::stringstream sstr;
    sstr << "Take(" << name << "): Can't change status from "
         << as_string(*status) << " to " << as_string(new_status);
    throw std::invalid_argument(sstr.str());
  }
}
