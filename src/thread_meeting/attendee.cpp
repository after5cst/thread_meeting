#include "attendee.h"
#include <memory>


void Attendee::bind(pybind11::module& m)
{
    pybind11::class_<Attendee, Attendee::pointer_t>(m, "Attendee")
        .def("__repr__",
            [](const Attendee &a) {
                return "<thread_Meeting.Attendee '" + a.name + "'>";
            }
            );
}
