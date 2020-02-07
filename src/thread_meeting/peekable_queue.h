#ifndef _PEEKABLE_QUEUE
#define _PEEKABLE_QUEUE
#include <chrono>
#include <deque>
#include <memory>
#include <queue>

#include "globals.h"

class PeekableQueue {
public:
  enum class Options { enable_append, disable_append };

  PeekableQueue(Options options = Options::enable_append)
      : m_disable_append(options == Options::disable_append), m_high(),
        m_medium(), m_low() {}
  typedef std::shared_ptr<PeekableQueue> pointer_t;
  static void bind(pybind11::module &);

  void append(pybind11::object obj, int delay_in_seconds);
  bool empty();
  void push(pybind11::object obj, int delay_in_seconds, bool can_purge = true);
  pybind11::object head();
  pybind11::object get();

private:
  struct low_t {
    std::chrono::steady_clock::time_point when =
        std::chrono::steady_clock::now();
    pybind11::object what = pybind11::none();
    bool operator<(const low_t &other) const { return when > other.when; }
  };

  const bool m_disable_append;
  std::deque<pybind11::object> m_high;
  std::deque<pybind11::object> m_medium;
  std::priority_queue<low_t> m_low;
};

#endif // _PEEKABLE_QUEUE
