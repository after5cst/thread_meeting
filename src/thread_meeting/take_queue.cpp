#include "take_queue.h"

void TakeQueue::bind(pybind11::module& m)
{
    pybind11::class_<TakeQueue, TakeQueue::pointer_t>(m, "TakeQueue")
        .def(pybind11::init<>())
        .def_property_readonly("head", &TakeQueue::head)
        .def("append", &TakeQueue::append)
        .def("get", &TakeQueue::head)
        .def("__repr__",
            [](const TakeQueue &a) {
                return "<thread_meeting.TakeQueue>";
            }
            );
}

void TakeQueue::append( Take::pointer_t take )
{
    m_queue.push_back(take);
}

pybind11::object TakeQueue::head() const
{
    return m_queue.empty() ? pybind11::none() : pybind11::cast(m_queue.front());
}

pybind11::object TakeQueue::get()
{
    pybind11::object result = pybind11::none();
    if (!m_queue.empty())
    {
        result = pybind11::cast(m_queue.front());
        m_queue.pop_front();
    }
    return result;
}
