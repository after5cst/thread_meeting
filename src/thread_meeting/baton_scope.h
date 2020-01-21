#ifndef _BATON_SCOPE
#define _BATON_SCOPE
#include "baton.h"
#include "enter_exit.h"

class BatonScope : public EnterExitImpl<Baton> {
  typedef EnterExitImpl<Baton> baseclass;

public:
  BatonScope(bool valid) : baseclass(), m_valid(valid) {}

  virtual pointer_t set_target() override;
  virtual void clear_target(pointer_t &target) override;

private:
  bool m_valid;
};

#endif // _BATON_SCOPE
