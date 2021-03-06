#ifndef ATTENDEE_H
#define ATTENDEE_H
#include "globals.h"
#include <deque>
#include <memory>
#include <stack>

#include "baton_scope.h"
#include "keep.h"
#include "priority_queue.h"
#include "take.h"

class Attendee : public std::enable_shared_from_this<Attendee> {
public:
  typedef std::shared_ptr<Attendee> pointer_t;
  static void bind(pybind11::module &);

  std::unique_ptr<EnterExit> create_iterruptable_scope(pybind11::object);
  std::unique_ptr<EnterExit> request_baton();
  std::unique_ptr<Keep> note(std::string name, pybind11::object payload,
                             float delay_in_seconds);

  void add_to_queue(Take::pointer_t take, float delay_in_seconds);

  std::string name = std::string();
  PriorityQueue::pointer_t queue = std::make_shared<PriorityQueue>();
  bool valid = true;

  pybind11::object pop_interrupt_class() {
    auto result = pybind11::none();
    if (!m_interruptables.empty()) {
      result = m_interruptables.top();
      m_interruptables.pop();
    }
    return result;
  }

  void push_interrupt_class(pybind11::object top) {
    m_interruptables.push(top);
  }

  bool is_admin = false;
  bool has_baton() const;
  thread_id_t thread_id() const { return m_thread_id; }

private:
  const thread_id_t m_thread_id = PyThread_get_thread_ident();
  std::stack<pybind11::object> m_interruptables =
      std::stack<pybind11::object>();
};

#endif // ATTENDEE_H
