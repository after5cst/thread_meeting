#ifndef _PEEKABLE_QUEUE
#define _PEEKABLE_QUEUE
#include <chrono>
#include <deque>
#include <memory>
#include <queue>

#include "globals.h"

class PriorityQueue {
public:
  PriorityQueue() : m_high_q(), m_low_q(), m_future_q() {}
  typedef std::shared_ptr<PriorityQueue> pointer_t;
  static void bind(pybind11::module &);

  bool empty();
  void push_high(pybind11::object obj);
  void push_low(pybind11::object obj);
  void push_future(pybind11::object obj, float delay_in_seconds);
  pybind11::object get(bool purge_if_high);

private:
  struct low_t {
    std::chrono::steady_clock::time_point when =
        std::chrono::steady_clock::now();
    pybind11::object what = pybind11::none();
    bool operator<(const low_t &other) const { return when > other.when; }
  };

  std::deque<pybind11::object> m_high_q;
  std::deque<pybind11::object> m_low_q;
  std::priority_queue<low_t> m_future_q;
};

#endif // _PEEKABLE_QUEUE
