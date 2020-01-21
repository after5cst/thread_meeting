#ifndef _TRANSCIPTION_SCOPE
#define _TRANSCIPTION_SCOPE
#include "enter_exit.h"
#include "peekable_queue.h"

class TranscriptScope : public EnterExitImpl<PeekableQueue> {
  typedef EnterExitImpl<PeekableQueue> baseclass;

public:
  virtual pointer_t set_target() override;
  virtual void clear_target(pointer_t &target) override;
};

#endif // _TRANSCIPTION_SCOPE
