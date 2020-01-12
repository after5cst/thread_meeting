#include "attendee.h"
#include "join.h"
#include "keep.h"
#include "take.h"

PYBIND11_MODULE(thread_meeting, m) {
    m.doc() = R"pbdoc(
        thread_meeting plugin
        -----------------------

        .. currentmodule:: thread_meeting

        .. autosummary::
           :toctree: _generate

           Attendee
           Join
           Keep
           Take
    )pbdoc";

    Attendee::bind(m);
    Join::bind(m);
    Keep::bind(m);
    Take::bind(m);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
