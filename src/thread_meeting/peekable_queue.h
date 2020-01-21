#ifndef _PEEKABLE_QUEUE
#define _PEEKABLE_QUEUE
#include <deque>
#include <memory>

#include "globals.h"

class PeekableQueue {
public:
  enum class Options { enable_append, disable_append };

  PeekableQueue(Options options = Options::enable_append)
      : m_disable_append(options == Options::disable_append), m_queue() {}
  typedef std::shared_ptr<PeekableQueue> pointer_t;
  static void bind(pybind11::module &);

  void append(pybind11::object obj);
  bool empty() const { return m_queue.empty(); }
  void push(pybind11::object obj);
  pybind11::object head() const;
  pybind11::object get();

private:
  const bool m_disable_append;
  std::deque<pybind11::object> m_queue;
};

#endif // _PEEKABLE_QUEUE
