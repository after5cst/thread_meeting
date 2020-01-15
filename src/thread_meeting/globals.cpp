#include "globals.h"
#include "pybind11/pybind11.h"

#include <sstream>

attendees_t g_attendees;
std::weak_ptr< Baton > g_baton;

long get_python_thread_id()
{
    auto state = PyGILState_GetThisThreadState();
    if (NULL == state)
    {
        throw std::runtime_error("Python thread state not found");
    }
    return state->thread_id;
}

bool verify_python_thread_id(long expected_id, bool throw_if_not)
{
    auto thread_id = get_python_thread_id();
    auto verified = thread_id == expected_id;
    if (throw_if_not && (!verified))
    {
        std::stringstream sstr;
        sstr << "Object use exclusive to Python thread "
             << expected_id
             << " (caller attempted on thread "
             << thread_id
             << ")";
        throw std::runtime_error(sstr.str());
    }
    return verified;
}
