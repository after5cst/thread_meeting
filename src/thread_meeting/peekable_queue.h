#ifndef _PEEKABLE_QUEUE
#define _PEEKABLE_QUEUE
#include <memory>
#include <deque>

#include "pybind11/pybind11.h"


class PeekableQueue
{
public:
    typedef std::shared_ptr<PeekableQueue> pointer_t;
    static void bind(pybind11::module&);
    
    void append(pybind11::object obj);
    bool empty() const { return m_queue.empty(); }
    pybind11::object head() const;
    pybind11::object get();
private:
    std::deque<pybind11::object> m_queue;
};

#endif // _PEEKABLE_QUEUE
