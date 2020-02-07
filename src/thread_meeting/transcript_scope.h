#ifndef _TRANSCIPTION_SCOPE
#define _TRANSCIPTION_SCOPE
#include "enter_exit.h"
#include "priority_queue.h"

class TranscriptScope : public EnterExitImpl<PriorityQueue> {
  typedef EnterExitImpl<PriorityQueue> baseclass;

public:
  virtual pointer_t set_target() override;
  virtual void clear_target(pointer_t &target) override;
};

#endif // _TRANSCIPTION_SCOPE
