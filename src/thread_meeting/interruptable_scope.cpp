#include "interruptable_scope.h"

#include "globals.h"

InterruptableScope::pointer_t InterruptableScope::set_target() {
  auto target = m_creator.lock();
  if (target) {
    transcribe("Interruptable", TranscriptType::enter);
    target->push_interrupt_class(m_exception_class);
  }
  return target;
}

void InterruptableScope::clear_target(pointer_t &target) {
  if (target) {
    transcribe("Interruptable", TranscriptType::exit);
    target->pop_interrupt_class();
    target.reset();
  }
}
