#include "attendee.h"
#include "enter_exit.h"

class AttendeeScope : public EnterExitImpl<Attendee> {
  typedef EnterExitImpl<Attendee> baseclass;

public:
  AttendeeScope(std::string attendee_name, bool is_admin)
      : baseclass(), m_name(attendee_name), m_is_admin(is_admin) {}

  virtual pointer_t set_target() override;
  virtual void clear_target(pointer_t &target) override;

  std::string m_name;
  bool m_is_admin;
};
