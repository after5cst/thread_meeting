#ifndef ATTENDEE_H
#define ATTENDEE_H
#include <deque>
#include <memory>
#include <pybind11/pybind11.h>

#include "baton_scope.h"
#include "keep.h"
#include "peekable_queue.h"
#include "take.h"

class Attendee {
public:
  typedef std::shared_ptr<Attendee> pointer_t;
  static void bind(pybind11::module &);

  std::unique_ptr<EnterExit> request_baton();
  std::unique_ptr<Keep> note(std::string name, pybind11::object payload);

  void add_to_queue(Take::pointer_t take);

  std::string name;

  Attendee() {
    queue =
        std::make_shared<PeekableQueue>(PeekableQueue::Options::disable_append);
  }
  bool valid = true;
  PeekableQueue::pointer_t queue;

private:
  const thread_id_t m_thread_id = PyThread_get_thread_ident();
};

#endif // ATTENDEE_H
