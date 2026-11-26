class Rules {
 public:
  virtual ~Rules() = default;
  virtual int limit() const { return 10; }
};

class StrictRules : public Rules {
 public:
  int limit() const override { return 5; }
};

class FixedRules : public Rules {
 public:
  int limit() const final { return 1; }
};
