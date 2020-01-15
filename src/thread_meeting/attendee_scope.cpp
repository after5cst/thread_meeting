#include "attendee_scope.h"
#include "attendee.h"

#include <sstream>

bool AttendeeScope::name_conflicts(const std::string& name) const
{
    for (const auto info: g_attendees)
    {
        if (auto ptr = info.second.lock())
        {
            if (name == ptr->name)
            {
                return true;
            }
        }
    }
    return false;
}


AttendeeScope::pointer_t AttendeeScope::set_target()
{
    if (auto ptr = g_attendees[thread_id()].lock())
    {
        auto msg =  "Attendee '" +  ptr->name + "' already present";
        throw std::runtime_error(msg);
    }

    if (0 == m_name.size())
    {
        std::stringstream sstr;
        sstr << "Thread " << thread_id();
        m_name = sstr.str();
        if (name_conflicts(m_name))
        {
            m_name = "Unknown";
        }
    }

    auto name = m_name;
    for (auto i = 0; name_conflicts(name); ++i)
    {
        std::stringstream sstr;
        sstr << m_name << " " << i;
        name = sstr.str();
    }

    auto target = std::make_shared<Attendee>();
    target->name = name;
    g_attendees[thread_id()] = target;
    return target;
}

void AttendeeScope::clear_target(pointer_t& target)
{
    g_attendees.erase(thread_id());
    target->valid = false;
    target.reset();
}
