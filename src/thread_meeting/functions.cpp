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
      .value(as_string(MessageStatus::pending), MessageStatus::pending)
      .value(as_string(MessageStatus::acknowledged),
             MessageStatus::acknowledged)
      .value(as_string(MessageStatus::protested), MessageStatus::protested);

  pybind11::enum_<TranscriptType>(m, "TranscriptType", pybind11::arithmetic())
      .value(as_string(TranscriptType::ack), TranscriptType::ack)
      .value(as_string(TranscriptType::custom), TranscriptType::custom)
      .value(as_string(TranscriptType::enter), TranscriptType::enter)
      .value(as_string(TranscriptType::exit), TranscriptType::exit)
      .value(as_string(TranscriptType::nack), TranscriptType::nack)
      .value(as_string(TranscriptType::note), TranscriptType::note)
      .value(as_string(TranscriptType::post), TranscriptType::post)
      .value(as_string(TranscriptType::recv), TranscriptType::recv)
      .value(as_string(TranscriptType::state), TranscriptType::state);

  m.def("participate", &participate, pybind11::arg("attendee_name") = "");
  m.def("me", &me);
  m.def("starting_baton", starting_baton);
  m.def("transcribe", &python_transcribe, pybind11::arg("message"),
        pybind11::arg("ti_type") = TranscriptType::custom);
  m.def("transcriber", &transcriber);
}
