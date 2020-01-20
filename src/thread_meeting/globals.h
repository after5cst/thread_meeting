#ifndef _GLOBALS_H
#define _GLOBALS_H
#include <memory>
#include <unordered_map>
#include "pybind11/pybind11.h"

#if PY_VERSION_HEX >= 0x03070000
    // In Python 3.7, the type of PyThread_get_thread_ident()
    // changed from long to unsigned long.
    typedef unsigned long thread_id_t ;
#else
    typedef long thread_id_t;
#endif

class Attendee;
class Baton;
class PeekableQueue;

enum class ThreadState {
    unknown, idle, working, busy, presenter
};
enum class TranscriptType {
    ack, custom, enter, exit, nack, note, post, recv, send, state
};
enum class MessageStatus {
    pending, acknowledged, protested
};

typedef std::unordered_map< thread_id_t, std::shared_ptr<Attendee> > attendees_t;
typedef std::unordered_map< thread_id_t, std::shared_ptr<PeekableQueue> > transcripts_t;

extern attendees_t g_attendees;
extern std::weak_ptr< Baton > g_baton;
extern thread_id_t g_initial_thread_id;
extern transcripts_t g_transcripts;

std::string as_string(const MessageStatus& status);

std::string verify_thread_name(std::string suggested_name = std::string());
bool verify_python_thread_id(thread_id_t expected_id, bool throw_if_not=true);
pybind11::object transcribe(std::string message,
                            TranscriptType transcript_type);


#endif // _GLOBALS_H
