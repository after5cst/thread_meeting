#include "keep.h"
#include "take.h"

#include <sstream>

void Keep::bind(pybind11::module& m)
{
    pybind11::class_<Keep>(m, "Keep")
        .def(pybind11::init<std::string, pybind11::object>(),
             pybind11::arg("name") = "",
             pybind11::arg("payload") = pybind11::none())
        .def("create_take", &Keep::create_take)
        .def_readonly("name", &Keep::name)
        .def_readonly("payload", &Keep::payload)
        .def_property_readonly("acknowledged", &Keep::acknowledged)
        .def_property_readonly("pending", &Keep::pending)
        .def_property_readonly("protested", &Keep::protested)
        .def("__repr__",
            [](const Keep &a) {
                return "<thread_meeting.Keep '" + a.name + "'>";
            }
            );
}

Take::pointer_t Keep::create_take()
{
    auto ptr = std::make_shared<Take>(name, payload);
    m_deque.push_back(ptr->status);
    return ptr;
}


int Keep::acknowledged() const
{
    auto result = 0;
    for (const auto& item : m_deque)
    {
        if (MessageStatus::acknowledged == *item)
        {
            ++result;
        }
    }
    return result;
}

int Keep::pending() const
{
    auto result = 0;
    for (const auto& item : m_deque)
    {
        if (MessageStatus::pending == *item)
        {
            ++result;
        }
    }
    return result;
}

int Keep::protested() const
{
    auto result = 0;
    for (const auto& item : m_deque)
    {
        if (MessageStatus::protested == *item)
        {
            ++result;
        }
    }
    return result;
}
