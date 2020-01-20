#ifndef ATTENDEE_H
#define ATTENDEE_H
#include <deque>
#include <memory>
#include <pybind11/pybind11.h>

#include "baton_scope.h"
#include "keep.h"
#include "peekable_queue.h"
#include "take.h"

class Attendee
{
public:
    typedef std::shared_ptr<Attendee> pointer_t;
    static void bind(pybind11::module&);

    std::unique_ptr<EnterExit> request_baton();
    ThreadState current_state() const;
    std::unique_ptr<Keep> add_to_queue(
            std::string name, pybind11::object payload);

    std::string name;
    bool valid = true;
    PeekableQueue::pointer_t queue = std::make_shared<PeekableQueue>(
        PeekableQueue::Options::disable_append);
private:
    mutable ThreadState m_last_state = ThreadState::unknown;
};

#endif // ATTENDEE_H
