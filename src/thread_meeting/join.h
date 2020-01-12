#ifndef JOIN_H
#define JOIN_H
#include "attendee.h"

long get_python_thread_id();
bool verify_python_thread_id(long expected_id, bool throw_if_not=true);

class Join
{
public:
    Join(std::string attendee_name_);
    static void bind(pybind11::module&);

    // Python access methods.
    Attendee::pointer_t on_enter();
    pybind11::object on_exit(pybind11::object exc_type,
                             pybind11::object exc_value,
                             pybind11::object traceback);

    std::string attendee_name;
private:
    long python_thread_id = 0;
    Attendee::pointer_t attendee;
};

#endif // JOIN_H
