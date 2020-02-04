#include "baton.h"

#include "attendee.h"

void Baton::bind(pybind11::module &m) {
  pybind11::class_<Baton, Baton::pointer_t> o(m, "Baton",
                                              R"pbdoc(
The object that allows the owner to post messages to Attendees.

A Baton can only be owned by one worker at a time, and is created through
the context manager returned from either the primary_baton() function
or the Attendee.request_baton() method.

A Baton can not be directly created from Python code without use of
one of the above functions.
)pbdoc");

  o.def("__bool__", [](const Baton &a) { return a.valid(); },
        R"pbdoc(
Returns True if the Baton is valid, False otherwise.

An Baton is considered valid if it is still within the scope
of the ContextManager that created it.

This attribute is read-only.
)pbdoc");

  o.def("__repr__", [](const Baton &) { return "<thread_Meeting.Baton>"; });

  o.def("post", &Baton::post,
        R"pbdoc(
Put an item in all other Attendee queues.

If the Attendee is interruptable, schedule the related exception to be
raised in the Attendee's thread.

:param message: A string describing the post.
:param payload: An optional object passed with the note.  Not commonly used.

:return: The Keep object associated with the post.
)pbdoc",
        pybind11::arg("message"), pybind11::arg("payload") = pybind11::none());
}

std::unique_ptr<Keep> Baton::post(std::string name, pybind11::object payload) {
  if (!valid()) {
    throw std::runtime_error("Baton is out of scope, cannot post()");
  }
  auto keep = std::make_unique<Keep>(name, payload);
  for (auto &item : g_attendees) {
    if (item.first != m_owner_thread_id) // We don't post to ourselves.
    {
      auto take = keep->create_take();
      item.second->add_to_queue(take);
    }
  }
  return keep;
}
