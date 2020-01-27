#ifndef INTERRUPTABLESCOPE_H
#define INTERRUPTABLESCOPE_H
#include "attendee.h"
#include "enter_exit.h"

class InterruptableScope : public EnterExitImpl<Attendee> {
  typedef EnterExitImpl<Attendee> baseclass;

public:
  InterruptableScope(Attendee::pointer_t creator,
                     pybind11::object exception_class)
      : baseclass(), m_creator(creator), m_exception_class(exception_class) {}

  virtual pointer_t set_target() override;
  virtual void clear_target(pointer_t &target) override;

private:
  std::weak_ptr<Attendee> m_creator;
  pybind11::object m_exception_class;
};
#endif // INTERRUPTABLESCOPE_H
