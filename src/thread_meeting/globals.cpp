#include "globals.h"
#include "pybind11/pybind11.h"

#include <sstream>

attendees_t g_attendees;
std::weak_ptr< Baton > g_baton;
std::shared_ptr<PeekableQueue> g_transcription;
thread_id_t g_initial_thread_id = 0;

bool verify_python_thread_id(thread_id_t expected_id, bool throw_if_not)
{
    auto thread_id = PyThread_get_thread_ident();
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
