#include "functions.h"
#include "attendee_scope.h"
#include "globals.h"
#include "transcript_item.h"
#include "transcript_scope.h"

std::unique_ptr<EnterExit> transcriber() {
  return std::make_unique<TranscriptScope>();
}

std::unique_ptr<EnterExit> starting_baton() {
  // We only can create a starting baton if the room is empty
  // (no attendees yet).
  return std::make_unique<BatonScope>(g_attendees.size() == 0);
}

std::unique_ptr<EnterExit> participate(std::string attendee_name) {
  return std::make_unique<AttendeeScope>(attendee_name);
}

pybind11::object me() {
  pybind11::object result = pybind11::none();
  auto id = PyThread_get_thread_ident();
  auto iter = g_attendees.find(id);
  if (iter != g_attendees.end()) {
    result = pybind11::cast(iter->second);
  }
  return result;
}

// Provided since Python doesn't need access to destination.
pybind11::object python_transcribe(std::string message,
                                   TranscriptType transcript_type) {
  auto result = transcribe(message, transcript_type, 0);
  return result;
}

pybind11::object transcribe(std::string message, TranscriptType transcript_type,
                            thread_id_t destination) {
  if (0 == g_transcripts.size()) {
    return pybind11::none();
  }
  auto item =
      pybind11::cast(TranscriptItem(message, transcript_type, destination));

  for (auto &transcript : g_transcripts) {
    transcript.second->push(item);
  }
  return item;
}

void bind_functions(pybind11::module &m) {
  pybind11::enum_<MessageStatus>(m, "TakeStatus", pybind11::arithmetic())
      .value(as_string(MessageStatus::pending), MessageStatus::pending,
             "Message has not been picked up by queue owner")
      .value(as_string(MessageStatus::acknowledged),
             MessageStatus::acknowledged,
             "Message was picked up by queue owner and was not protested")
      .value(as_string(MessageStatus::protested), MessageStatus::protested,
             "Message was picked up by queue owner and owner protested");

  pybind11::enum_<TranscriptType>(m, "TranscriptType", pybind11::arithmetic())
      .value(as_string(TranscriptType::ack), TranscriptType::ack,
             "Positive acknowledgement of entry")
      .value(as_string(TranscriptType::custom), TranscriptType::custom,
             "Entry is of unknown (script-generated) type")
      .value(as_string(TranscriptType::debug), TranscriptType::debug,
             "Entry is a debug message")
      .value(as_string(TranscriptType::enter), TranscriptType::enter,
             "Entry notes the start of element in message")
      .value(as_string(TranscriptType::exit), TranscriptType::exit,
             "Entry notes the end of element in message")
      .value(as_string(TranscriptType::nack), TranscriptType::nack,
             "Negative acknowledgement of entry")
      .value(as_string(TranscriptType::note), TranscriptType::note,
             "Entry notes queue item posted by the queue owner")
      .value(as_string(TranscriptType::post), TranscriptType::post,
             "Entry notes queue item posted by a non-queue owner")
      .value(as_string(TranscriptType::recv), TranscriptType::recv,
             "Entry has been received")
      .value(as_string(TranscriptType::state), TranscriptType::state,
             "Entry denotes a state change by owner");

  m.def("participate", &participate,
        R"pbdoc(
Create a Context Manager that provides an Attendee to the thread.

Each thread may have one and only one Attendee.  When a thread
calls participate, it is joined to the meeting with the provided name.

While the thread is in the meeting, the Attendee may have items added
to the queue that were placed there by itself or by another Attendee
who has the Baton.

:param attendee_name: The requested name of the attendee.  If the name
    is a duplicate, a numeric suffix will be added to make it unique.

:return: A Context Manager that will provide an Attendee on entry and
    invalidate the attendee on exit.
)pbdoc",
        pybind11::arg("attendee_name") = "");

  m.def("me", &me,
        R"pbdoc(
Return the Attendee already attached to this thread via participate().

Each thread may have one and only one Attendee.  When this method is
called, it will return the Attendee object associated with the calling
thread.

:return: The Attendee object.  If there is no Attendee object for
         the thread, returns None.
)pbdoc");

  m.def("starting_baton", starting_baton,
        R"pbdoc(
Return the Baton object prior to any threads joining the meeting.

In order for the main thread to send a message to start the meeting,
this function returns the Baton object.  If there are any members
already in the meeting, None is returned.

:return: The Baton object.  If there is any Attendee in the
         meeting, returns None.
)pbdoc");

  m.def("transcribe", &python_transcribe,
        R"pbdoc(
Add an entry to the Transcript.

:param message: The string to add to the transcript in the
        Message field.
:param ti_type: The TranscriptType to add to the transcript
        in the ti_type field.

:return: The TranscriptItem added to the Transcript.
)pbdoc",
        pybind11::arg("message"),
        pybind11::arg("ti_type") = TranscriptType::custom);

  m.def("transcriber", &transcriber,
        R"pbdoc(
Create a Context Manager that provides a Transcript to the thread.

A Transcript receives any TranscriptItems placed for the meeting via
the transcribe() function.

This context manager provides a queue where every TranscriptItem
will be placed for the life of the context manager.

:return: A Context Manager that will provide the Transcript
        for the meeting, which is a PeekableQueue.
)pbdoc");
}
