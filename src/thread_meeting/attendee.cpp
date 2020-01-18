#include "attendee.h"
#include "baton_scope.h"

#include <memory>


void Attendee::bind(pybind11::module& m)
{
    pybind11::class_<Attendee, Attendee::pointer_t>(m, "Attendee")
        .def("__repr__",
            [](const Attendee &a) {
                return "<thread_Meeting.Attendee '" + a.name + "'>";
            })
            .def_readonly("name", &Attendee::name)
            .def_readonly("valid", &Attendee::valid)
            .def_property_readonly("queue",
                [](const Attendee &a) {
                return pybind11::cast(a.queue);
                })
            .def("request_baton", &Attendee::request_baton)
            ;
}

std::unique_ptr<EnterExit> Attendee::request_baton()
{
    return std::make_unique< BatonScope >(valid);
}

ThreadState Attendee::current_state() const
{
    auto result = ThreadState::unknown;
    if (valid)
    {

    }
    if (result != m_last_state)
    {
        m_last_state = result;
    }
    return result;
}
