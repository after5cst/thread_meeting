#include "baton.h"

void Baton::bind(pybind11::module& m)
{
    pybind11::class_<Baton, Baton::pointer_t>(m, "Baton")
        .def("__repr__",
            [](const Baton &a) {
                return "<thread_Meeting.Baton>";
            })
            .def_property_readonly("valid", &Baton::valid)
            ;
}
