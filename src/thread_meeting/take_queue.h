#ifndef _TAKE_QUEUE
#define _TAKE_QUEUE
#include <memory>
#include <deque>

#include "pybind11/pybind11.h"
#include "take.h"


class TakeQueue
{
public:
    typedef std::unique_ptr<TakeQueue> pointer_t;
    static void bind(pybind11::module&);

    TakeQueue() = default;
    
    void append( Take::pointer_t take );
    pybind11::object head() const;
    pybind11::object get();
private:
    std::deque<Take::pointer_t> m_queue;
};

#endif // _TAKE_QUEUE