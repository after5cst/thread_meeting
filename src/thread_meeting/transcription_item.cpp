#include "transcription_item.h"

#include "attendee.h"

#include "pybind11/chrono.h"
#include <sstream>

void TranscriptionItem::bind(pybind11::module& m)
{
    pybind11::class_<TranscriptionItem, TranscriptionItem::pointer_t>(
                m, "TranscriptionItem")
        .def(pybind11::init<std::string, TranscriptionType>(),
             pybind11::arg("message") = "",
             pybind11::arg("message_type") = TranscriptionType::custom)
        .def("__repr__",
            [](const TranscriptionItem &a) {
                return "<thread_Meeting.TranscriptionItem>";
            })
        .def_readonly("source", &TranscriptionItem::source)
        .def_readonly("message", &TranscriptionItem::message)
        .def_readonly("message_type", &TranscriptionItem::message_type)
        .def_readonly("timestamp", &TranscriptionItem::timestamp)
        ;
}

TranscriptionItem::TranscriptionItem(std::string message_in,
                                     TranscriptionType transcription_type)
    : message(message_in),
      message_type(transcription_type),
      timestamp(pybind11::cast(std::chrono::system_clock::now()))
{
    if (message_in.size() == 0)
    {
        throw std::invalid_argument("Message may not be empty.");
    }

    auto id = PyThread_get_thread_ident();
    auto iter = g_attendees.find(id);
    Attendee::pointer_t ptr;
    if (iter != g_attendees.end())
    {
        ptr = iter->second.lock();
    }

    if (ptr)
    {
        source = ptr->name;
    }
    else if (id == g_initial_thread_id)
    {
        // Not registered, but it is the first thread to load this
        // module.  I don't want to call it 'main' (because it might
        // not be the main thread), but I will call it 'primary'
        // assuming that the primary thread loads this module first.
        source = "(primary)";
    }
    else
    {
        // This thread isn't registered.  Just use (Python thread ID)
        // for the source name.
        std::stringstream sstr;
        sstr << "(" << id << ")";
        source = std::move(sstr.str());
    }
}
