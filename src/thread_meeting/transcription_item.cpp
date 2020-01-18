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

    source = verify_thread_name(std::string());
}
