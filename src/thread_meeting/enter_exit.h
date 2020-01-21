#ifndef ENTER_EXIT_H
#define ENTER_EXIT_H
#include "globals.h"
#include <iostream>

class EnterExit {
public:
  static void bind(pybind11::module &);
  virtual ~EnterExit() = default;

  virtual pybind11::object on_enter() = 0;
  virtual pybind11::object on_exit(pybind11::object exc_type,
                                   pybind11::object exc_value,
                                   pybind11::object traceback) = 0;
};

template <typename T> class EnterExitImpl : public EnterExit {
public:
  typedef std::shared_ptr<T> pointer_t;
  virtual pybind11::object on_enter() override {
    verify_python_thread_id(m_python_thread_id);
    if (m_target) {
      throw std::runtime_error("object in use by ContextManager");
    }
    m_target = set_target();
    return m_target ? pybind11::cast(m_target) : pybind11::none();
  }
  virtual pybind11::object on_exit(pybind11::object, // exc_type
                                   pybind11::object, // exc_value,
                                   pybind11::object  // traceback
                                   ) override {
    clear_target(m_target);
    return pybind11::none();
  }

protected:
  virtual pointer_t set_target() = 0;
  // {
  //     return std::make_shared<T>();
  // }
  virtual void clear_target(pointer_t &target) = 0;
  // {
  //     target.reset();
  // }
  thread_id_t thread_id() const { return m_python_thread_id; }

private:
  thread_id_t m_python_thread_id = PyThread_get_thread_ident();
  pointer_t m_target = pointer_t();
};

#endif // ENTER_EXIT_H
