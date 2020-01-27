#include "attendee_scope.h"
#include "attendee.h"

#include <sstream>

AttendeeScope::pointer_t AttendeeScope::set_target() {
  // Ensure the name is unique.
  m_name = verify_thread_name(m_name);

  auto &attendee = g_attendees[thread_id()];

  if (attendee) {
    auto msg = "Attendee '" + attendee->name + "' already present";
    throw std::runtime_error(msg);
  }

  auto target = std::make_shared<Attendee>();
  target->name = m_name;
  attendee = target;

  std::stringstream sstr;
  sstr << "Thread ID: " << thread_id();
  transcribe(sstr.str(), TranscriptType::enter);
  return target;
}

void AttendeeScope::clear_target(pointer_t &target) {
  if (target) {
    std::stringstream sstr;
    sstr << "Thread ID: " << thread_id();
    transcribe(sstr.str(), TranscriptType::exit);

    g_attendees.erase(thread_id());
    target->valid = false;
    target.reset();
  }
}
