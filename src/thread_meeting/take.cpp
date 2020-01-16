#include "take.h"

void Take::bind(pybind11::module& m)
{
    pybind11::enum_<Take::Status>(m, "TakeStatus", pybind11::arithmetic())
            .value("Pending", Take::Status::pending)
            .value("Acknowledged", Take::Status::acknowledged)
            .value("Protested", Take::Status::protested)
            ;

    pybind11::class_<Take, Take::pointer_t>(m, "Take")
        .def(pybind11::init<std::string, pybind11::object>())
        .def_readonly("name", &Take::name)
        .def_property_readonly("status",
            [](Take &a) {
                return *(a.status);
            })
        .def("acknowledge", &Take::acknowledge)
        .def("protest", &Take::protest)
        .def("__repr__",
            [](const Take &a) {
                return "<thread_meeting.Take '" + a.name + "'>";
            }
            );
}
