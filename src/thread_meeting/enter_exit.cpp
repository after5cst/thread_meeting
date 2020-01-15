#include "enter_exit.h"

#include <memory>
#include <sstream>

void EnterExit::bind(pybind11::module& m)
{
    pybind11::class_<EnterExit>(m, "_EnterExit")
        .def("__enter__", &EnterExit::on_enter)
        .def("__exit__", &EnterExit::on_exit, // exit_help,
             pybind11::arg("exc_type"), pybind11::arg("exc_value"),
             pybind11::arg("traceback"))
        .def("__repr__",
            [](const EnterExit &) {
                return "<thread_meeting._EnterExit>";
            }
            );
}
