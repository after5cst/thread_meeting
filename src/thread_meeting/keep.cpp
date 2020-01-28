#include "keep.h"
#include "take.h"

#include <sstream>

void Keep::bind(pybind11::module &m) {
  pybind11::class_<Keep> o(m, "Keep", R"pbdoc(
A Container to track related Take objects.

A Keep can create Take objects to send to other recipients, typically
in other threads.  Those  Take objects are automatically updated
when the recipient marks them as Acknowledged or Protested or the
object goes out of scope.

This allows the Keep holder to monitor what Takes are still outstanding.
and whatever steps are necessary to disable the object in __exit__.
)pbdoc");

  o.def(pybind11::init<std::string, pybind11::object>(),
        R"pbdoc(
Initialization function.

:param name: The name to be assigned to the Keep and all Take objects
             created from the Keep.
:param payload: The optional payload, which is accessible to the Take
             and related Keep objects.
)pbdoc",
        pybind11::arg("name") = "",
        pybind11::arg("payload") = pybind11::none());

  o.def("create_take", &Keep::create_take,
        R"pbdoc(
Returns a created Take object related to the Keep.

A Keep object can create Take objects that are meant to be consumed by other
clients (typically in other threads).  The Keep object is updated as those
Take(s) are consumed so it can know when the message passing is complete.

        :returns: A newly-created Take object related to the Keep.
)pbdoc");

  o.def_readonly("name", &Keep::name,
                 R"pbdoc(
The name passed to the Keep during initialization.
This attribute is read-only.
)pbdoc");

  o.def_readonly("payload", &Keep::payload,
                 R"pbdoc(
The payload passed to the Keep during initialization.
This attribute is read-only.
)pbdoc");

  o.def_property_readonly("acknowledged", &Keep::acknowledged,
                          R"pbdoc(
The number of related Takes that have been acknowledged.
This attribute is read-only.
)pbdoc");

  o.def_property_readonly("pending", &Keep::pending,
                          R"pbdoc(
The number of related Takes that are still pending.
This attribute is read-only.
)pbdoc");

  o.def_property_readonly("protested", &Keep::protested,
                          R"pbdoc(
The number of related Takes that have been protested.
This attribute is read-only.
)pbdoc");

  o.def("__repr__",
        [](const Keep &a) { return "<thread_meeting.Keep '" + a.name + "'>"; });
}

Take::pointer_t Keep::create_take() {
  auto ptr = std::make_shared<Take>(name, payload);
  m_deque.push_back(ptr->status);
  return ptr;
}

int Keep::acknowledged() const {
  auto result = 0;
  for (const auto &item : m_deque) {
    if (MessageStatus::acknowledged == *item) {
      ++result;
    }
  }
  return result;
}

int Keep::pending() const {
  auto result = 0;
  for (const auto &item : m_deque) {
    if (MessageStatus::pending == *item) {
      ++result;
    }
  }
  return result;
}

int Keep::protested() const {
  auto result = 0;
  for (const auto &item : m_deque) {
    if (MessageStatus::protested == *item) {
      ++result;
    }
  }
  return result;
}
