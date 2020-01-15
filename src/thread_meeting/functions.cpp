#include "functions.h"
#include "attendee_scope.h"
#include "globals.h"

std::unique_ptr< EnterExit > participate(std::string attendee_name)
{
    return std::make_unique< AttendeeScope >(attendee_name);
}

pybind11::object me()
{
    pybind11::object result = pybind11::none();
    auto id = get_python_thread_id();
    auto iter = g_attendees.find(id);
    if (iter != g_attendees.end())
    {
        if (auto ptr = iter->second.lock())
        {
            result = pybind11::cast(ptr);
        }
    }
    return result;
}

void bind_functions(pybind11::module& m)
{
    m.def("participate", &participate, pybind11::arg("attendee_name") = "");
    m.def("me", &me);
}
