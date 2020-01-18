#ifndef _TRANSCIPTION_SCOPE
#define _TRANSCIPTION_SCOPE
#include "peekable_queue.h"
#include "enter_exit.h"

class TranscriptionScope : public EnterExitImpl<PeekableQueue>
{
    typedef EnterExitImpl<PeekableQueue> baseclass;
public:
    TranscriptionScope() : baseclass() {}

    virtual pointer_t set_target() override;
    virtual void clear_target(pointer_t& target) override;
};

#endif // _TRANSCIPTION_SCOPE
