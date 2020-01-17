#include "attendee.h"
#include "baton.h"
#include "enter_exit.h"
#include "functions.h"
#include "keep.h"
#include "take.h"
#include "peekable_queue.h"

//#include "attendee_scope.h"
//#include "baton_scope.h"

PYBIND11_MODULE(thread_meeting, m) {
    m.doc() = R"pbdoc(
        thread_meeting plugin
        -----------------------

        .. currentmodule:: thread_meeting

        .. autosummary::
           :toctree: _generate

           attend
           Attendee
           Keep
           Take
    )pbdoc";

    bind_functions(m);
    Attendee::bind(m);
    Baton::bind(m);
    EnterExit::bind(m);
    Keep::bind(m);
    Take::bind(m);
    PeekableQueue::bind(m);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
