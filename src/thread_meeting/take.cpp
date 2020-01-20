#include "take.h"

#include "globals.h"

#include <sstream>


void Take::bind(pybind11::module& m)
{
    pybind11::class_<Take, Take::pointer_t>(m, "Take")
        .def(pybind11::init<std::string, pybind11::object>())
        .def_readonly("name", &Take::name)
        .def_property_readonly("status",
            [](Take &a) {
                return *(a.status);
            })
        .def("acknowledge", &Take::acknowledge)
        .def_readonly("payload", &Take::payload)
        .def("protest", &Take::protest)
        .def("__repr__",
            [](const Take &a) {
                return "<thread_meeting.Take '" + a.name + "'>";
            }
            );
}

void Take::set_status(MessageStatus new_status, bool throw_on_error)
{
    if (*status == new_status)
    {
        // Do nothing: setting a status to itself is a NOOP.
        return;
    }

    auto trans_type = TranscriptType::custom;
    switch (new_status)
    {
        case MessageStatus::acknowledged:
            if (MessageStatus::pending == *status)
            {
                trans_type = TranscriptType::ack;
            }
            break;
        case MessageStatus::protested:
            if (MessageStatus::pending == *status)
            {
                trans_type = TranscriptType::nack;
            }
            break;
        case MessageStatus::pending:
            break;
    }

    if (TranscriptType::custom != trans_type)
    {
        transcribe(name, trans_type);
        *status = new_status;

    }
    // If we reach here, there is an error.
    else if (throw_on_error)
    {
        std::stringstream sstr;
        sstr << "Take(" << name << "): Can't change status from "
            << as_string(*status) << " to "
            << as_string(new_status);
        throw std::invalid_argument(sstr.str());
    }
}
