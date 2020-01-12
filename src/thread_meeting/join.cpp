#include "join.h"

#include <memory>
#include <sstream>

typedef std::unordered_map< long, std::weak_ptr<Attendee> > attendees_t;
static attendees_t attendees;

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

void Join::bind(pybind11::module& m)
{
    pybind11::class_<Join>(m, "Join")
        .def(pybind11::init<std::string>(),
             pybind11::arg("attendee_name") = "")
        .def_readonly("suggested_name", &Join::attendee_name)
        .def("__enter__", &Join::on_enter)
        .def("__exit__", &Join::on_exit, // exit_help,
             pybind11::arg("exc_type"), pybind11::arg("exc_value"),
             pybind11::arg("traceback"))
        .def("__repr__",
            [](const Join &a) {
                return "<thread_meeting.Join '" + a.attendee_name + "'>";
            }
            );
}

Join::Join(std::string attendee_name_)
    : attendee_name(attendee_name_), python_thread_id(get_python_thread_id())
{
    if (auto attendee = attendees[python_thread_id].lock())
    {
        // Start simple: only one join allowed at a time on a thread.
        auto msg = "Meeting already joined on this thread by '"
                + attendee->name + "'";
        throw std::invalid_argument(msg);
    }
    if (0 == attendee_name.size())
    {
        std::stringstream sstr;
        sstr << "Thread " << python_thread_id;
        attendee_name = sstr.str();
    }
}

Attendee::pointer_t Join::on_enter()
{
    verify_python_thread_id(python_thread_id);
    if (attendee)
    {
        throw std::runtime_error("__join__ already called");
    }

    if (attendees[python_thread_id].lock())
    {
        std::stringstream sstr;
        sstr << "Meeting already joined on thread " << python_thread_id;
        throw std::runtime_error(sstr.str());
    }

    auto name = attendee_name;
    auto name_conflicts = true;
    for (auto i = 0; name_conflicts; ++i)
    {
        name_conflicts = false;
        for (const auto& item : attendees)
        {
            auto attendee = item.second.lock();
            if (attendee && attendee->name == name)
            {
                name_conflicts = true;
                break;
            }
        }
        if (name_conflicts)
        {
            std::stringstream sstr;
            sstr << attendee_name << " " << i;
            name = sstr.str();
        }
    }

    attendee = std::make_shared<Attendee>(name);
    attendees[python_thread_id] = attendee;
    return attendee;
}

pybind11::object Join::on_exit(pybind11::object /*exc_type*/,
                               pybind11::object /*exc_value*/,
                               pybind11::object /*traceback*/)
{
    if (verify_python_thread_id(python_thread_id, false))
    {
        attendee.reset();
    }
    return pybind11::none();
}
