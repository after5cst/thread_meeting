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

std::unique_ptr<Take> Keep::create_take(std::string name)
{
    auto ptr = std::make_unique<Take>(name, payload);
//    auto new_item = std::pair< std::string, Take::status_t >(
//                name, ptr->status);
//    auto insert_result = m_map.insert(new_item);
    auto insert_result = m_map.insert({name, ptr->status});
    if (!insert_result.second)
    {
        std::stringstream sstr;
        sstr << "Duplicate take name '" << name << "'";
        throw std::invalid_argument(sstr.str());
    }
    return ptr;
}


pybind11::list Keep::acknowledged() const
{
    auto result = pybind11::list();
    for (const auto& item : m_map)
    {
        if (Take::Status::acknowledged == *item.second)
            result.append(pybind11::str(item.first));
    }
    return result;
}

pybind11::list Keep::pending() const
{
    auto result = pybind11::list();
    for (const auto& item : m_map)
    {
        if (Take::Status::pending == *item.second)
            result.append(pybind11::str(item.first));
    }
    return result;
}

pybind11::list Keep::protested() const
{
    auto result = pybind11::list();
    for (const auto& item : m_map)
    {
        if (Take::Status::protested == *item.second)
            result.append(pybind11::str(item.first));
    }
    return result;
}
