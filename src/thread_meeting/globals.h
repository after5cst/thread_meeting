#ifndef _GLOBALS_H
#define _GLOBALS_H
#include <memory>
#include <unordered_map>

class Attendee;
class Baton;

typedef std::unordered_map< long, std::weak_ptr<Attendee> > attendees_t;
extern attendees_t g_attendees;

extern std::weak_ptr< Baton > g_baton;

long get_python_thread_id();
bool verify_python_thread_id(long expected_id, bool throw_if_not=true);

#endif // _GLOBALS_H
