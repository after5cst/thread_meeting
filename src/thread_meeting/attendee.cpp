#include "attendee.h"
#include "baton_scope.h"
#include "interruptable_scope.h"

#include <memory>

void Attendee::bind(pybind11::module &m) {
  pybind11::class_<Attendee, Attendee::pointer_t> o(m, "Attendee", R"pbdoc(
The object signifying a thread's participation in a meeting.

An Attendee is specific to a particular thread, and is created through
the context manager returned from a participate() call.

While an Attendee is valid (during the scope of the participate() context
manager), a reference to the Attendee object can also be retrieved through
a call to the me() function.

An Attendee can not be directly created from Python code without use of
one of the above functions.
)pbdoc");

  o.def("__repr__", [](const Attendee &a) {
    return "<thread_Meeting.Attendee '" + a.name + "'>";
  });

  o.def_readonly("name", &Attendee::name, R"pbdoc(
The name of the Attendee.

A name is requested by the creator in the particpate() function.
If it is unique, it is used.  Otherwise, a number is appended
to make it unique.

This attribute is read-only.
)pbdoc");

  o.def("note", &Attendee::note, R"pbdoc(
Put an item in the Attendee queue from the Attendee's thread.

An exception is raised if the note is attempted to be placed
from any other thread.  To post messages across all workers,
the caller must use the Baton from request_baton().

:param message: A string describing the note.
:param payload: An optional object passed with the note.  Not commonly used.
:param delay_in_sec: The minimum number of seconds before the item can
        be picked up from the queue (defaults to zero).

:return: The Keep object associated with the posted note.
)pbdoc",
        pybind11::arg("message"), pybind11::arg("payload") = pybind11::none(),
        pybind11::arg("delay_in_sec") = 0.0);

  o.def_property_readonly(
      "queue", [](const Attendee &a) { return pybind11::cast(a.queue); },
      R"pbdoc(
The PriorityQueue for the Attendee.

The queue contains messages sent to the Attendee either via the note()
method (within the Attendee's thread) or the Baton.post() method (from
other threads).  Items cannot be directly added to the queue via its
append() method.

:param message: A string describing the note.
:param payload: An optional object passed with the note.  Not commonly used.

:return: The Keep object associated with the posted note.

This attribute is read-only.
)pbdoc");

  o.def("__bool__", [](const Attendee &a) { return a.valid; },
        R"pbdoc(
Returns True if the Attendee is valid, False otherwise.

An Attendee is considered valid if it is still within the scope
of the ContextManager that created it.  The package function
participate() provides the ContextManager.

This attribute is read-only.
)pbdoc");

  o.def("interrupt_with", &Attendee::create_iterruptable_scope,
        R"pbdoc(
Returns a Context Manager that provides scoping for interrupts.

When an Attendee has messages placed in the queue from the Baton,
the other thread may optionally raise an exception in the Attendee's
thread to notify the Attendeee's thread immediately that its
queue is not empty.

Within the scope of the conxtext manager returned from the function,
the Attendee is willing to have an exception raised of the specified
class provided by the caller when an item is posted to its queue.

The note() function will not raise an exception even in this case,
as the caller is the Attendee thread itself and should be aware
that the queue is not empty after the note() calll.

:param exception_class: The exception class (not the exception object)
    that should be instantiated and raised when a message is posted.
)pbdoc",
        pybind11::arg("exception_class"));

  o.def("request_baton", &Attendee::request_baton,
        R"pbdoc(
Try to get the Baton so the caller can post messages to other queues.

The Baton is an object that can only be held by a single thread at a time.
While the Baton is held, the thread can use it to post messages to other
Attendee's queues.

This function returns a Context Manager that provides the Baton for the
duration of the scop if the Baton is available.  If the Baton is not available,
the Context Manager will return None on __enter__.

:returns: A Context Manager for the Baton object
)pbdoc");
}

void Attendee::add_to_queue(Take::pointer_t take, float delay_in_seconds) {
  auto thread_id = PyThread_get_thread_ident();
  auto trans_type = TranscriptType::post_low;
  auto priority = Priority::low;
  if (0 < delay_in_seconds) {
    trans_type = TranscriptType::post_future;
    priority = Priority::future;
  } else if (thread_id != m_thread_id) {
    trans_type = TranscriptType::post_high;
    priority = Priority::high;
  }

  transcribe(take->name, trans_type, m_thread_id);
  auto python_take = pybind11::cast(take);
  switch (priority) {
  case Priority::future:
    queue->push_future(python_take, delay_in_seconds);
    break;
  case Priority::high:
    queue->push_high(python_take);
    break;
  case Priority::low:
    queue->push_low(python_take);
    break;
  }

  // The message has been pushed.  Now, fire an exception on the
  // target Python thread if they have an interruptable to fire.
  if (!(thread_id == m_thread_id || m_interruptables.empty())) {
    auto top = m_interruptables.top();
    PyThreadState_SetAsyncExc(m_thread_id, top.ptr());
  }
}

bool Attendee::has_baton() const {
  if (auto baton = g_baton.lock()) {
    return m_thread_id == baton->get_owner_thead_id();
  }
  return false;
}

std::unique_ptr<Keep> Attendee::note(std::string name, pybind11::object payload,
                                     float delay_in_seconds) {
  verify_python_thread_id(m_thread_id);
  auto keep = std::make_unique<Keep>(name, payload);
  auto take = keep->create_take();
  add_to_queue(take, delay_in_seconds);
  return keep;
}

std::unique_ptr<EnterExit>
Attendee::create_iterruptable_scope(pybind11::object obj) {
  return std::make_unique<InterruptableScope>(shared_from_this(), obj);
}

std::unique_ptr<EnterExit> Attendee::request_baton() {
  return std::make_unique<BatonScope>(valid);
}
