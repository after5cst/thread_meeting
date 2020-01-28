#include "enter_exit.h"

#include <memory>
#include <sstream>

void EnterExit::bind(pybind11::module &m) {
  pybind11::class_<EnterExit> o(m, "_EnterExit", R"pbdoc(
A Context Manager object.

An _EnterExit object enables the functionality of the object
it returns from the __enter__ method and disables the
functionality of the object in the __exit__ method.  This
ensures clean resource cleanup and lifespace of the object.

An _EnterExit object can be thought of as a 'base' class, with
the the derived class controlling what object is returned from __enter__
and whatever steps are necessary to disable the object in __exit__.
)pbdoc");

  o.def("__enter__", &EnterExit::on_enter,
        R"pbdoc(
The Context Manager entry method.

:returns: An object that is enabled until the __exit__ method is
        called on the _EntryExit object.
)pbdoc");

  o.def("__exit__", &EnterExit::on_exit,
        R"pbdoc(
The Context Manager exit method.

This will disable the object returned from the __enter__ method.

:param exc_type:  The exception type if any, otherwise None
:param exc_value: The exception value if any, otherwise None
:param traceback: The traceback if any, otherwise None

:returns: None
)pbdoc",
        pybind11::arg("exc_type"), pybind11::arg("exc_value"),
        pybind11::arg("traceback"));

  o.def("__repr__",
        [](const EnterExit &) { return "<thread_meeting._EnterExit>"; });
}
