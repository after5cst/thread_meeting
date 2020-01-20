#include "baton.h"

#include "attendee.h"

void Baton::bind(pybind11::module& m)
{
    pybind11::class_<Baton, Baton::pointer_t>(m, "Baton")
        .def("__repr__",
            [](const Baton &a) {
                return "<thread_Meeting.Baton>";
            })
            .def_property_readonly("valid", &Baton::valid)
            ;
}

std::unique_ptr<Keep> Baton::post(std::string name,
                                  pybind11::object payload)
{
    if (!valid())
    {
        throw std::runtime_error("Baton is out of scope, cannot post()");
    }
    auto keep = std::make_unique<Keep>(name, payload);
    for (auto& item : g_attendees)
    {
        if (item.first != m_owner_thread_id) // We don't post to ourselves.
        {
            auto take = keep->create_take(name);
            item.second->add_to_queue(take);
        }
    }
    return keep;
}
