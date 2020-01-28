#include "globals.h"

#include "attendee.h"

#include <assert.h>
#include <sstream>

attendees_t g_attendees;
std::weak_ptr<Baton> g_baton;
thread_id_t g_initial_thread_id = 0;
transcripts_t g_transcripts;

const char *as_string(const MessageStatus &status) {
  switch (status) {
  case MessageStatus::acknowledged:
    return "Acknowledged";
  case MessageStatus::pending:
    return "Pending";
  case MessageStatus::protested:
    return "Protested";
  }
  assert(false);
  return "";
}

const char *as_string(const TranscriptType &trans_type) {
  switch (trans_type) {
  case TranscriptType::ack:
    return "Ack";
  case TranscriptType::custom:
    return "Custom";
  case TranscriptType::debug:
    return "Debug";
  case TranscriptType::enter:
    return "Enter";
  case TranscriptType::exit:
    return "Exit";
  case TranscriptType::nack:
    return "Nack";
  case TranscriptType::note:
    return "Note";
  case TranscriptType::post:
    return "Post";
  case TranscriptType::recv:
    return "Recv";
  case TranscriptType::send:
    return "Send";
  case TranscriptType::state:
    return "State";
  }
  assert(false);
  return "";
}

bool verify_python_thread_id(thread_id_t expected_id, bool throw_if_not) {
  auto thread_id = PyThread_get_thread_ident();
  auto verified = thread_id == expected_id;
  if (throw_if_not && (!verified)) {
    std::stringstream sstr;
    sstr << "Object use exclusive to Python thread " << expected_id
         << " (caller attempted on thread " << thread_id << ")";
    throw std::runtime_error(sstr.str());
  }
  return verified;
}

std::string verify_thread_name(std::string suggested_name, thread_id_t id) {
  if (0 == id) {
    id = PyThread_get_thread_ident();
  }

  // First pass: if the thread has an attendee with a name,
  // it *IS* the name, so just return it.
  for (auto &info : g_attendees) {
    const auto &attendee_id = info.first;
    const auto &attendee = info.second;
    if (attendee_id == id) {
      // Already have a name: use it.
      return attendee->name;
    }
  }

  // There is no already-defined name for this thread.
  // If the suggested name is empty, then make one up.
  if (suggested_name.size()) {
    // deliberately empty!
  } else if (id == g_initial_thread_id) {
    // Not registered, but it is the first thread to load this
    // module.  I don't want to call it 'main' (because it might
    // not be the main thread), but I will call it 'primary'
    // assuming that the primary thread loads this module first.
    suggested_name = "(primary)";
  } else {
    // This thread isn't registered.  Just use (Python thread ID)
    // for the suggested name.
    std::stringstream sstr;
    sstr << "(" << id << ")";
    suggested_name = sstr.str();
  }

  // Second pass: Try `suggested_name` (and then `suggested_name1`,
  //    `suggested_name2`, ...) until a unique name is found.
  auto name = suggested_name;
  for (auto i = 1; i; ++i) {
    for (auto &info : g_attendees) {
      const auto &attendee = info.second;
      if (name == attendee->name) {
        // This name already in use: suggestion is invalid.
        name.clear();
        break;
      }
    }
    if (name.size()) {
      // name still set, it is unique.  We are done.
      break;
    } else {
      // The name was not unique: append a suffix and try again.
      std::stringstream sstr;
      sstr << suggested_name << i;
      name = sstr.str();
    }
  }

  return name;
}
