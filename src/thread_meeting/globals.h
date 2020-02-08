#ifndef _GLOBALS_H
#define _GLOBALS_H

// pybind11 generates a number of warnings.  Since we compile
// with warnings as errors, disable the warnings.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Weffc++"
#include "pybind11/pybind11.h"
#pragma GCC diagnostic pop

#include <memory>
#include <unordered_map>

#if PY_VERSION_HEX >= 0x03070000
// In Python 3.7, the type of PyThread_get_thread_ident()
// changed from long to unsigned long.
typedef unsigned long thread_id_t;
#else
typedef long thread_id_t;
#endif

class Attendee;
class Baton;
class PriorityQueue;

enum class TranscriptType {
  ack,
  custom,
  debug,
  drop,
  enter,
  exit,
  nack,
  post_future,
  post_high,
  post_low,
  recv,
  send,
  state
};
enum class MessageStatus { pending, acknowledged, protested };
enum class Priority { future, low, high };

typedef std::unordered_map<thread_id_t, std::shared_ptr<Attendee>> attendees_t;
typedef std::unordered_map<thread_id_t, std::shared_ptr<PriorityQueue>>
    transcripts_t;

extern std::weak_ptr<Attendee> g_admin;
extern attendees_t g_attendees;
extern std::weak_ptr<Baton> g_baton;
extern thread_id_t g_initial_thread_id;
extern transcripts_t g_transcripts;

const char *as_string(const MessageStatus &status);
const char *as_string(const Priority &priority);
const char *as_string(const TranscriptType &transcript_type);

std::string verify_thread_name(std::string suggested_name = std::string(),
                               thread_id_t thread_id = 0);
bool verify_python_thread_id(thread_id_t expected_id, bool throw_if_not = true);
pybind11::object transcribe(std::string message, TranscriptType transcript_type,
                            thread_id_t destination = 0);

#endif // _GLOBALS_H
